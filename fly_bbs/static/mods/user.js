/**

 @Name: 用户模块

 */
 
layui.define(['laypage', 'fly', 'element', 'flow'], function(exports){

  var $ = layui.jquery;
  var layer = layui.layer;
  var util = layui.util;
  var laytpl = layui.laytpl;
  var form = layui.form;
  var laypage = layui.laypage;
  var fly = layui.fly;
  var flow = layui.flow;
  var element = layui.element;
  var upload = layui.upload;

  var gather = {}, dom = {
    mine: $('#LAY_mine')
    ,mineview: $('.mine-view')
    ,minemsg: $('#LAY_minemsg')
    ,infobtn: $('#LAY_btninfo')
  };

  //我的相关数据
  var elemUC = $('#LAY_uc'), elemUCM = $('#LAY_ucm');
  gather.minelog = {};
  gather.mine = function(index, type, url){
    var tpl = [
      //求解
        // <i>{{ layui.util.timeAgo(d.rows[i].create_at["$date"], 1) }} 收藏</i>
      '{{# for(var i = 0; i < d.rows.length; i++){ }}\
      <li>\
        {{# if(d.type === "collection"){ }}\
          <a class="jie-title" href="/post/{{d.rows[i]._id}}/" target="_blank">{{= d.rows[i].title}}</a>\
        {{# } else { }}\
          {{# if(d.rows[i].is_cream){ }}\
          <span class="fly-jing layui-hide-xs">精</span>\
          {{# } }}\
          {{# if(d.rows[i].is_closed){ }}\
            <span class="jie-status jie-status-ok">已结</span>\
          {{# } else { }}\
            <span class="jie-status">未结</span>\
          {{# } }}\
          <a class="jie-title" href="/post/{{d.rows[i]._id}}/" target="_blank">{{= d.rows[i].title}}</a>\
          <i class="layui-hide-xs">{{ layui.util.timeAgo(d.rows[i].create_at.$date, 1) }}</i>\
          {{# if(!d.rows[i].is_closed){ }}\
          <a class="mine-edit layui-hide-xs" href="/edit/{{d.rows[i]._id}}" target="_blank">编辑</a>\
          {{# } }}\
          <em class="layui-hide-xs">{{d.rows[i].view_count || 0}}阅/{{d.rows[i].comment_count || 0}}答</em>\
        {{# } }}\
      </li>\
      {{# } }}'
    ];

    var view = function(res){
      var html = laytpl(tpl[0]).render(res);
      dom.mine.children().eq(index).find('span').html(res.count);
      elemUCM.children().eq(index).find('ul').html(res.rows.length === 0 ? '<div class="fly-msg">没有相关数据</div>' : html);
    };

    var page = function(now){
      var curr = now || 1;
      if(gather.minelog[type + '-page-' + curr]){
        view(gather.minelog[type + '-page-' + curr]);
      } else {
        //我收藏的帖
        if(type === 'collection'){
          var nums = 10; //每页出现的数据量
          fly.json(url, {}, function(res){
            res.count = res.rows.length;

            var rows = layui.sort(res.rows, 'create_at', 'desc')
            ,render = function(curr){
              var data = []
              ,start = curr*nums - nums
              ,last = start + nums - 1;

              if(last >= rows.length){
                last = curr > 1 ? start + (rows.length - start - 1) : rows.length - 1;
              }

              for(var i = start; i <= last; i++){
                // rows[i].create_at = util.toDateString(rows[i].create_at["$date"], "yyyy-MM-dd HH:mm:ss")
                data.push(rows[i]);
              }

              res.rows = data;
              res.type = 'collection';
              res.rows.forEach(function (row) {
                  row['_id'] = row['_id']['$oid']
              })
              view(res);
            };

            render(curr)
            gather.minelog['collect-page-' + curr] = res;

            now || laypage.render({
              elem: 'LAY_page1'
              ,count: rows.length
              ,curr: curr
              ,jump: function(e, first){
                if(!first){
                  render(e.curr);
                }
              }
            });
          });
        } else {
          fly.json('/api/'+ type +'/' + curr, function(res){
            res.type = 'post';

              res.rows.forEach(function (row) {
                  row['_id'] = row['_id']['$oid']
              })
            view(res);
            gather.minelog['mine-jie-page-' + curr] = res;
            now || laypage.render({
              elem: 'LAY_page'
              ,count: res.count
              ,curr: curr
              ,jump: function(e, first){
                if(!first){
                  page(e.curr);
                }
              }
            });
          });
        }
      }
    };

    if(!gather.minelog[type]){
      page();
    }
  };

  if(elemUC[0]){
    layui.each(dom.mine.children(), function(index, item){
      var othis = $(item)
      gather.mine(index, othis.data('type'), othis.data('url'));
    });
  }

  //显示当前tab
  if(location.hash){
    element.tabChange('user', location.hash.replace(/^#/, ''));
  }

  element.on('tab(user)', function(){
    var othis = $(this), layid = othis.attr('lay-id');
    if(layid){
      location.hash = layid;
    }
  });

  //根据ip获取城市
  if($('#L_city').val() === ''){
    $.getScript('http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=js', function(){
      $('#L_city').val(remote_ip_info.city||'');
    });
  }

  //上传图片
  if($('.upload-img')[0]){
    layui.use('upload', function(upload){
      var avatarAdd = $('.avatar-add');

      //开启图床
      upload.render({
        elem: '.upload-img'
        ,url: '/api/upload'
          ,field:'smfile'
        ,size: 50
        ,before: function(){
          avatarAdd.find('.loading').show();
        }
        ,done: function(res){
          if(res.code == 0){
            $.post('/user/set', {
              avatar: res.data.url
            }, function(res){
              location.reload();
            });
          } else {
            layer.msg(res.msg, {icon: 5});
          }
          avatarAdd.find('.loading').hide();
        }
        ,error: function(){
          avatarAdd.find('.loading').hide();
        }
      });
    });
  }

  //合作平台
  if($('#LAY_coop')[0]){

    //资源上传
    $('#LAY_coop .uploadRes').each(function(index, item){
      var othis = $(this);
      upload.render({
        elem: item
        ,url: '/api/upload/cooperation/?filename='+ othis.data('filename')
        ,accept: 'file'
        ,exts: 'zip'
        ,size: 30*1024
        ,before: function(){
          layer.msg('正在上传', {
            icon: 16
            ,time: -1
            ,shade: 0.7
          });
        }
        ,done: function(res){
          if(res.code == 0){
            layer.msg(res.msg, {icon: 6})
          } else {
            layer.msg(res.msg)
          }
        }
      });
    });

    //成效展示
    var effectTpl = ['{{# layui.each(d.data, function(index, item){ }}'
    ,'<tr>'
      ,'<td><a href="/u/{{ item.uid }}" target="_blank" style="color: #01AAED;">{{ item.uid }}</a></td>'
      ,'<td>{{ item.authProduct }}</td>'
      ,'<td>￥{{ item.rmb }}</td>'
      ,'<td>{{ item.create_time }}</td>'
      ,'</tr>'
    ,'{{# }); }}'].join('');

    var effectView = function(res){
      var html = laytpl(effectTpl).render(res);
      $('#LAY_coop_effect').html(html);
      $('#LAY_effect_count').html('你共有 <strong style="color: #FF5722;">'+ (res.count||0) +'</strong> 笔合作授权订单');
    };

    var effectShow = function(page){
      fly.json('/cooperation/effect', {
        page: page||1
      }, function(res){
        effectView(res);
        laypage.render({
          elem: 'LAY_effect_page'
          ,count: res.count
          ,curr: page
          ,jump: function(e, first){
            if(!first){
              effectShow(e.curr);
            }
          }
        });
      });
    };

    effectShow();

  }

  //提交成功后刷新
  fly.form['set-mine'] = function(data, required){
    layer.msg('修改成功', {
      icon: 1
      ,time: 1000
      ,shade: 0.1
    }, function(){
      location.reload();
    });
  }

  //帐号绑定
  $('.acc-unbind').on('click', function(){
    var othis = $(this), type = othis.attr('type');
    layer.confirm('整的要解绑'+ ({
      qq_id: 'QQ'
      ,weibo_id: '微博'
    })[type] + '吗？', {icon: 5}, function(){
      fly.json('/api/unbind', {
        type: type
      }, function(res){
        if(res.status === 0){
          layer.alert('已成功解绑。', {
            icon: 1
            ,end: function(){
              location.reload();
            }
          });
        } else {
          layer.msg(res.msg);
        }
      });
    });
  });


  //我的消息
  gather.minemsg = function(){
    var delAll = $('#LAY_delallmsg')
    ,delEnd = function(clear){
      if(clear || dom.minemsg.find('.mine-msg li').length === 0){
        dom.minemsg.html('<div class="fly-none">您暂时没有最新消息</div>');
      }
    }
    
    //阅读后删除
    dom.minemsg.on('click', '.mine-msg li .fly-delete', function(){
      var othis = $(this).parents('li'), id = othis.data('id');
      fly.json('/user/message/remove', {
        id: id
      }, function(res){
        if(res.status === 0){
          othis.fadeOut();
          setTimeout(function () {
              othis.remove();
              delEnd();
          }, 1500)

        }
      });
    });

    //删除全部
    $('#LAY_delallmsg').on('click', function(){
      var othis = $(this);
      layer.confirm('确定清空吗？', function(index){
        fly.json('/user/message/remove', {
          all: true
        }, function(res){
          if(res.status === 0){
            layer.close(index);
            othis.addClass('layui-hide');
            delEnd(true);
          }
        });
      });
    });

  };

  dom.minemsg[0] && gather.minemsg();

  exports('user', null);
  
});